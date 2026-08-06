keys_sorted = (sorted(item_dict.keys()))
if len(keys_sorted) != 0:
    new_key = keys_sorted[-1] + 1
else:
    new_key = 0
item_dict.update({new_key:{
    "type" : "text",
    "originator": variable, 
    "display_text" :"hello world", 
    }})

