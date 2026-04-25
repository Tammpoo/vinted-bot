import db
import requests
from pyVintedVN import Vinted, requester
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from logger import get_logger

logger = get_logger(__name__)


def process_query(query, name=None):
    parsed_url = urlparse(query)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) >= 2 and path_parts[0] == "brand":
        brand_id_with_name = path_parts[1]
        brand_id = brand_id_with_name.split("-")[0]
        new_path = "/catalog"
        new_query_params = {"brand_ids[]": [brand_id]}
        new_query_string = urlencode(new_query_params, doseq=True)
        query = urlunparse(
            (parsed_url.scheme, parsed_url.netloc, new_path, "", new_query_string, "")
        )
        logger.info(f"Converted brand URL to standard format: {query}")
        parsed_url = urlparse(query)

    query_params = parse_qs(parsed_url.query)
    query_params["order"] = ["newest_first"]
    query_params.pop("time", None)
    query_params.pop("search_id", None)
    query_params.pop("disabled_personalization", None)
    query_params.pop("page", None)

    new_query = urlencode(query_params, doseq=True)
    processed_query = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    if db.is_query_in_db(processed_query) is True:
        return "Query already exists.", False
    else:
        db.add_query_to_db(processed_query, name)
        return "Query added.", True


def get_formatted_query_list():
    all_queries = db.get_queries()
    queries_keywords = []
    for query in all_queries:
        parsed_url = urlparse(query[1])
        query_params = parse_qs(parsed_url.query)
        query_name = (
            query[3]
            if query[3] is not None
            else query_params.get("search_text", [None])[0]
        )
        if query_name is None:
            queries_keywords.append(query[1][:50])
        else:
            queries_keywords.append(query_name)

    if not queries_keywords:
        return ""
    query_list = "\n".join([str(i + 1) + ". " + j for i, j in enumerate(queries_keywords)])
    return query_list


def process_remove_query(number):
    if number == "all":
        db.remove_all_queries_from_db()
        return "All queries removed.", True

    if number.isdigit():
        db.remove_query_from_db(number)
        return "Query removed.", True
    else:
        return "Invalid number.", False


def process_update_query(query_id, query, name):
    parsed_url = urlparse(query)
    query_params = parse_qs(parsed_url.query)
    query_params["order"] = ["newest_first"]
    query_params.pop("time", None)
    query_params.pop("search_id", None)
    query_params.pop("disabled_personalization", None)
    query_params.pop("page", None)

    new_query = urlencode(query_params, doseq=True)
    processed_query = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    if db.update_query_in_db(query_id, processed_query, name):
        return "Query updated.", True
    else:
        return "Failed to update query.", False


def process_add_country(country):
    country = country.replace(" ", "")
    country_list = db.get_allowlist()

    if len(country) != 2:
        return "Invalid country code", country_list

    if country_list != 0 and country.upper() in country_list:
        return f'Country "{country.upper()}" already in allowlist.', country_list

    db.add_to_allowlist(country.upper())
    return "Country added.", db.get_allowlist()


def process_remove_country(country):
    country = country.replace(" ", "")

    if len(country) != 2:
        return "Invalid country code", db.get_allowlist()

    db.remove_from_allowlist(country.upper())
    return "Country removed.", db.get_allowlist()


def get_user_country(profile_id):
    url = f"https://www.vinted.it/api/v2/users/{profile_id}?localize=false"
    response = requester.get(url)
    if response.status_code == 429:
        url = f"https://www.vinted.it/api/v2/users/{profile_id}/items?page=1&per_page=1"
        response = requester.get(url)
        try:
            user_country = response.json()["items"][0]["user"]["country_iso_code"]
        except (KeyError, IndexError):
            logger.warning("Couldn't get the country due to rate limiting.")
            user_country = "XX"
    else:
        try:
            user_country = response.json()["user"]["country_iso_code"]
        except KeyError:
            user_country = "XX"
    return user_country


def process_items(queue):
    all_queries = db.get_queries()
    vinted = Vinted()
    items_per_query = int(db.get_parameter("items_per_query"))

    for query in all_queries:
        try:
            all_items = vinted.items.search(query[1], nbr_items=items_per_query)
            data = [item for item in all_items if item.is_new_item()]
            queue.put((data, query[0]))
            logger.info(f"Scraped {len(data)} items for query: {query[1][:60]}")
        except Exception as e:
            logger.error(f"Error scraping query {query[0]}: {e}")


def clear_item_queue(items_queue, new_items_queue):
    if not items_queue.empty():
        data, query_id = items_queue.get()
        banwords_str = db.get_parameter("banwords")
        for item in reversed(data):
            last_query_timestamp = db.get_last_timestamp(query_id)
            if (
                last_query_timestamp is not None
                and last_query_timestamp >= item.raw_timestamp
            ):
                pass
            elif db.is_item_in_db_by_id(item.id) is True:
                db.update_last_timestamp(query_id, item.raw_timestamp)
                pass
            elif db.get_allowlist() != 0 and (
                get_user_country(item.raw_data["user"]["id"])
            ) not in (db.get_allowlist() + ["XX"]):
                db.update_last_timestamp(query_id, item.raw_timestamp)
                pass
            elif banwords_str and contains_banwords(item.title, banwords_str):
                db.update_last_timestamp(query_id, item.raw_timestamp)
                pass
            else:
                message_template = db.get_parameter("message_template")
                content = message_template.format(
                    title=item.title,
                    price=str(item.price) + " " + item.currency,
                    brand=item.brand_title,
                )
                new_items_queue.put((content, item.url, "Open Vinted", None, None))
                db.add_item_to_db(
                    id=item.id,
                    timestamp=item.raw_timestamp,
                    price=item.price,
                    title=item.title,
                    photo_url=item.photo,
                    query_id=query_id,
                    currency=item.currency,
                )


def contains_banwords(title, banwords_str):
    banwords = [
        word.strip().lower() for word in banwords_str.split("|||") if word.strip()
    ]
    if not banwords:
        return False
    title_lower = title.lower()
    for word in banwords:
        if word in title_lower:
            return True
    return False


def check_version():
    try:
        github_url = db.get_parameter("github_url")
        ver = db.get_parameter("version")
        url = f"{github_url}/releases/latest"
        response = requests.get(url)

        if response.status_code == 200:
            latest_version = response.url.split("/")[-1]
            is_up_to_date = ver == latest_version
            return is_up_to_date, ver, latest_version, github_url
        else:
            return True, ver, ver, github_url
    except Exception as e:
        logger.error(f"Error checking for new version: {str(e)}")
        return True, "1.0.5", "1.0.5", "https://github.com/Fuyucch1/Vinted-Notifications"
