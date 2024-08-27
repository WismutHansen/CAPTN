import os

def get_folder_location():
    while True:
        folder_path = input("Enter the folder path: ")
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return folder_path
        else:
            print("Invalid folder path. Please try again.")

def get_keyword():
    while True:
        keyword = input("Enter the keyword to replace with: ")
        if len(keyword.strip()) > 0:
            return keyword
        else:
            print("Keyword cannot be empty. Please try again.")

def get_word_to_replace():
    while True:
        word_to_replace = input("Enter the word to replace: ")
        if len(word_to_replace.strip()) > 0:
            return word_to_replace
        else:
            print("Word to replace cannot be empty. Please try again.")

def replace_words_in_folder(folder_path, keyword, word_to_replace):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r+", encoding="utf-8") as file:
                text = file.read()
                new_text = text.replace(word_to_replace, keyword)
                file.seek(0)
                file.write(new_text)
                file.truncate()

def main():
    folder_path = get_folder_location()
    keyword = get_keyword()
    word_to_replace = get_word_to_replace()
    print(f"Replacing '{word_to_replace}' with '{keyword}' in {folder_path}...")
    replace_words_in_folder(folder_path, keyword, word_to_replace)
    print("Replacement complete!")

if __name__ == "__main__":
    main()