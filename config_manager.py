from RPA.Robocorp.WorkItems import WorkItems

class ConfigManager:
    env = "local"
    if env is "cloud":
        #WorkItems.get_input_work_item()
        SEARCH_PHRASE = WorkItems.get_work_item_variable("search_phrase")
        SECTIONS = WorkItems.get_work_item_variable("sections")
        MONTHS_NUMBER = WorkItems.get_work_item_variable("months_number")
    else:
        SEARCH_PHRASE = "ecuador"
        SECTIONS = ["new york"]
        MONTHS_NUMBER = 1

    BASE_URL = "https://www.nytimes.com/search?dropmab=false&endDate=[end_date]&query=[search_phrase]&sections=%2C[sections]&sort=newest&startDate=[start_date]"

    SECTION_CODES = {
        "any": "",
        "world": "World%7Cnyt%3A%2F%2Fsection%2F70e865b6-cc70-5181-84c9-8368b3a5c34b%2C",
        "u.s.": "U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c%2C",
        "new york": "New%20York%7Cnyt%3A%2F%2Fsection%2F39480374-66d3-5603-9ce1-58cfa12988e2%2C",
        "business": "Business%7Cnyt%3A%2F%2Fsection%2F0415b2b0-513a-5e78-80da-21ab770cb753%2C",
        "opinion": "Opinion%7Cnyt%3A%2F%2Fsection%2Fd7a71185-aa60-5635-bce0-5fab76c7c297%2C",
        "science": "Science%7Cnyt%3A%2F%2Fsection%2Ffb241e16-cbde-5d60-be6e-6bca9e86c697%2C",
        "health": "Health%7Cnyt%3A%2F%2Fsection%2F9f943015-a899-5505-8730-6d30ed861520%2C",
        "sports": "Sports%7Cnyt%3A%2F%2Fsection%2F4381411b-670f-5459-8277-b181485a19ec%2C",
        "arts": "Arts%7Cnyt%3A%2F%2Fsection%2F6e6ee292-b4bd-5006-a619-9ceab03524f2%2C",
        "books": "Books%7Cnyt%3A%2F%2Fsection%2F550f75e2-fc37-5d5c-9dd1-c665ac221b49%2C",
        "style": "Style%7Cnyt%3A%2F%2Fsection%2F146e2c45-6586-59ef-bc23-90e88fe2cf0a%2C",
        "food": "Food%7Cnyt%3A%2F%2Fsection%2F4f379b11-446b-57ae-8e2a-0cff12e0f26e%2C",
        "travel": "Travel%7Cnyt%3A%2F%2Fsection%2Fb2fb7c08-4f8e-5cff-8e14-aff8a49a9934%2C",
        "magazine": "Magazine%7Cnyt%3A%2F%2Fsection%2Fa913d1fb-3cdf-556b-9a81-f0b996a1a202%2C",
        "home & garden": "Home%20%26%20Garden%7Cnyt%3A%2F%2Fsection%2F1f56b6e8-73c6-5dab-a58e-18b96b0f366a%2C",
    }
