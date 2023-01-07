import random
import re

def strWithoutChar(fnSource,toReplace: str,value: str = " "):
    """Generation of a string from fnSource where value is put in place of substring found by regex toReplace"""

    return re.sub(toReplace,value,fnSource())

def randomElement(existingSource = None, randomSourceFn = None, args: list = [], template: str = None, alsoNaN: bool = False) -> any:
    possibilities = []
    if existingSource is not None: possibilities.append(0)
    if randomSourceFn != None: possibilities.append(1)
    if alsoNaN: possibilities.append(2)
    
    choice = random.choice(possibilities)
    if not choice:
        res = existingSource[random.randint(0,existingSource.size-1)]
    elif choice == 1:
        res = randomSourceFn(*args)
    else:
        return None
    
    return res if template == None else template.format(res)

def rndFormattedInt(min: int = 0, max: int = 10, template: str = None):
    return template.format(random.randint(min,max))