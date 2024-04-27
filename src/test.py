import regex
import re
# Regular expression to remove nested and non-nested brackets and parentheses
# We use a simpler non-recursive approach, suitable for one or two levels of nesting
pattern = re.compile(r'\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]|<[^<>]*>|『[^『』]*』|「[^「」]*」')


# Usage example: substituting the matched patterns with an empty string
text = "(2011Q1) 君に層け 2ND SEASON - 第02話「episode 2 2年生」(NTV 1280x720 x264)"
cleaned_text = pattern.sub('', text)
print(cleaned_text)
