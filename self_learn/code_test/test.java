def is_palindrome(text):
    text = text.lower().replace(" ", "")
    return text == text[::-1]

def count_vowels(text):
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)

def reverse_words(sentence):
    return " ".join(word[::-1] for word in sentence.split())

text = "Was it a car or a cat I saw"

print("Original:", text)
print("Is Palindrome?", is_palindrome(text))
print("Vowel Count:", count_vowels(text))
print("Reversed Words:", reverse_words(text))