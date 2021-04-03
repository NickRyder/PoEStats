"""re strings to help parse the different stat translations"""

"""±00.00%"""
re_number_pattern = r"\+?-?\d+\.?\d*\%?"
"""+#%"""
re_hashtag_pattern = r"\+?\#\%?"
"""+{0}%"""
re_insert_pattern = r"\+?{\d+}\%?"
re_insert_group_pattern = r"\+?{(\d+)}\%?"
