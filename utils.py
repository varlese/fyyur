#----------------------------------------------------------------------------#
# Utils
#----------------------------------------------------------------------------#

# Sanitize genre names for slugs
# Source = https://www.peterbe.com/plog/fastest-python-function-to-slugify-a-string

def slugify(text):
    """
    Turn the text content of a header into a slug for use in an ID
    """
    non_url_safe = ['"', '#', '$', '%', '&', '+',
                ',', '/', ':', ';', '=', '?',
                '@', '[', '\\', ']', '^', '`',
                '{', '|', '}', '~', "'"]
    non_safe = [c for c in text if c in non_url_safe]
    if non_safe:
        for c in non_safe:
            text = text.replace(c, '')
    # Strip leading, trailing and multiple whitespace, convert remaining whitespace to _
    text = u'_'.join(text.split())
    return text.lower()