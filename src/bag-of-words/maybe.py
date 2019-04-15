def multi_dict_gen():
    """
    Generates a dictionary of relevant words for each category classification 
    """

    # initializing category dictionary
    category_dict = {
        "Education": {},
        "Children": {},
        "Women and Girls": {},
        "Animals": {},
        "Climate Change": {},
        "Democracy and Governance": {},
        "Disaster Recovery": {},
        "Economic Development": {},
        "Environment": {},
        "Microfinance": {},
        "Health": {},
        "Humanitarian Assistance": {},
        "Human Rights": {},
        "Sport": {},
        "Technology": {},
        "Hunger": {},
        "Arts and Culture": {},
        "LGBTQAI+": {},
    }

    # opening scraped website data
    websites = db.get_dataset("organizations_text")
    project_sums = dynamo_db.get_dataset("project_summaries")

    # opening scraped website data
    with open("classifications/correct_classifications.json") as correct:
        classifications = json.load(correct)

        # processing words and inserting them into categories dictionary
        for i in range((int)(len(websites) * 0.8)):
            # grabbing and processing text
            website = websites[i]
            if website.get("text") is None:
                continue

            text = preprocess_text(website.get("text"))
            text = nltk.pos_tag(text)

            # putting words into dictionary
            for theme in classifications[website["name"]]["themes"]:
                temp_dict = dict(text)
                for word in temp_dict:
                    # counting the frequency of words to be used for scores later
                    try:
                        category_dict[theme["name"]][word]["freq"] += 1
                    except:
                        category_dict[theme["name"]][word] = {
                            "tags": temp_dict[word],
                            "freq": 1,
                        }
            print(i / (len(websites) * 0.8))

        i = 0
        for project in project_sums:
            text = preprocess_text(project["summary"])
            text = nltk.pos_tag(text)

            # putting words into dictionary
            temp_dict = dict(text)
            for word in temp_dict:
                # counting the frequency of words to be used for scores later
                try:
                    category_dict[project["theme"]][word]["freq"] += 1
                except:
                    category_dict[project["theme"]][word] = {
                        "tags": temp_dict[word],
                        "freq": 1,
                    }
            
            i += 1
            print(i / 25867)

        # calculating idf scores
        print("calculating idf scores...")
        calculate_idf_scores(category_dict)

    # dumping data
    with open("dictionaries/categories_dict.json", "w") as categories_json:
        json.dump(
            category_dict, categories_json, sort_keys=True, indent=2, ensure_ascii=False
        )

def remove_common_words_from_categories(categories):
    # creating dictionary of all unique words from categories
    all_words = set()
    for category in categories:
        all_words = all_words | set(categories[category].keys())

    all_words = dict.fromkeys(all_words, 0)

    # counting word freq in categories
    for category in categories:
        for word in categories[category].keys():
            all_words[word] += 1

    # removing words from categories with freq > 1 (non-unique words)
    for word in all_words:
        if all_words[word] > 1:
            for category in categories:
                categories[category].pop(word, None)

def print_category_classification_count(classifications):
    """
    Calculates the total number of classifications in each category
    """
    category_scores = {
        "Education": {"correct": 0, "total": 0},
        "Children": {"correct": 0, "total": 0},
        "Women and Girls": {"correct": 0, "total": 0},
        "Animals": {"correct": 0, "total": 0},
        "Climate Change": {"correct": 0, "total": 0},
        "Democracy and Governance": {"correct": 0, "total": 0},
        "Disaster Recovery": {"correct": 0, "total": 0},
        "Economic Development": {"correct": 0, "total": 0},
        "Environment": {"correct": 0, "total": 0},
        "Microfinance": {"correct": 0, "total": 0},
        "Health": {"correct": 0, "total": 0},
        "Humanitarian Assistance": {"correct": 0, "total": 0},
        "Human Rights": {"correct": 0, "total": 0},
        "Sport": {"correct": 0, "total": 0},
        "Technology": {"correct": 0, "total": 0},
        "Hunger": {"correct": 0, "total": 0},
        "Arts and Culture": {"correct": 0, "total": 0},
        "LGBTQAI+": {"correct": 0, "total": 0},
    }

    # determining total number of classifications in each category
    for org in classifications:
        for theme in classifications[org]["themes"]:
            category_scores[theme["name"]]["total"] += 1

    for category in category_scores:
        print(category + ": " + str(category_scores[category]["total"]))


def print_intersecting_categories(classifications):
    count = [[0 for i in range(18)] for j in range(7)]
    total = [[0 for i in range(18)] for j in range(7)]

    categories = {
        "Education": 0,
        "Children": 1,
        "Women and Girls": 2,
        "Animals": 3,
        "Climate Change": 4,
        "Democracy and Governance": 5,
        "Disaster Recovery": 6,
        "Economic Development": 7,
        "Environment": 8,
        "Microfinance": 9,
        "Health": 10,
        "Humanitarian Assistance": 11,
        "Human Rights": 12,
        "Sport": 13,
        "Technology": 14,
        "Hunger": 15,
        "Arts and Culture": 16,
        "LGBTQAI+": 17,
    }


    for org in classifications:
        themes = []
        for theme in classifications[org]["themes"]:
            themes.append(theme["name"])

        counter = 0
        for theme in themes:
            if (theme in ["Children", "Women and Girls", "Animals"]):
                counter += 1

        for theme in themes:
            if (not (theme in ["Children", "Women and Girls", "Animals"])):
                for i in range(7):
                    total[i][categories[theme]] += 1

                if (counter == 1):
                    if ("Children" in themes):
                        count[0][categories[theme]] += 1
                    elif("Women and Girls" in themes):
                        count[1][categories[theme]] += 1
                    else:
                        count[2][categories[theme]] += 1
                elif (counter == 2):
                    if (set(["Children", "Animals"]).issubset(themes)):
                        count[3][categories[theme]] += 1
                    elif (set(["Children", "Women and Girls"]).issubset(themes)):
                        count[4][categories[theme]] += 1
                    elif (set(["Women and Girls", "Animals"]).issubset(themes)):
                        count[5][categories[theme]] += 1
                elif (counter == 3):
                    count[6][categories[theme]] += 1


    for i in range(7):
        for j in range(18):
            if (j < 1 or j > 3):
                print("{:0.2f}".format(count[i][j] / total[i][j]) + " ", end="")
        print()


def print_category_dict_count(category_dict):
    # category word count
    category_count = {
        "Education": 0,
        "Children": 0,
        "Women and Girls": 0,
        "Animals": 0,
        "Climate Change": 0,
        "Democracy and Governance": 0,
        "Disaster Recovery": 0,
        "Economic Development": 0,
        "Environment": 0,
        "Microfinance": 0,
        "Health": 0,
        "Humanitarian Assistance": 0,
        "Human Rights": 0,
        "Sport": 0,
        "Technology": 0,
        "Hunger": 0,
        "Arts and Culture": 0,
        "LGBTQAI+": 0,
    }

    for category in category_dict:
        for word in category_dict[category]:
            category_count[category] += 1

    for category in category_count:
        print(category + ": " + str(category_count[category]))


def print_confusion_matrix(classifications):
    count = [[0 for i in range(18)] for j in range(18)]
    total = [[0 for i in range(18)] for j in range(18)]

    categories = {
        "Education": 0,
        "Children": 1,
        "Women and Girls": 2,
        "Animals": 3,
        "Climate Change": 4,
        "Democracy and Governance": 5,
        "Disaster Recovery": 6,
        "Economic Development": 7,
        "Environment": 8,
        "Microfinance": 9,
        "Health": 10,
        "Humanitarian Assistance": 11,
        "Human Rights": 12,
        "Sport": 13,
        "Technology": 14,
        "Hunger": 15,
        "Arts and Culture": 16,
        "LGBTQAI+": 17,
    }

    for org in classifications:
        themes = []
        for theme in classifications[org]["themes"]:
            themes.append(theme["name"])

        for theme in themes:
            for row in range(18):
                total[row][categories[theme]] += 1
            for theme_2 in themes:
                count[categories[theme]][categories[theme_2]] += 1

    for i in range(18):
        for j in range(18):
            print("{:0.2f}".format(count[i][j] / total[i][j]) + " ", end="")
        print()