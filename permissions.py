"""
Discord gives permissions as a decimal number. 
By converting to hex we can get the relevant permissions.

For example if the permission is 32792, we can convert it into 
hex 0x8018. This can be broken into the parts 0x8000, 0x0010, and 0x0008.
This gives us the permissions 'Attach Files', 'Manage Channels', 'Administrator' 
"""

class Permission():
    """
    This class abstracts the Discord Permissions into a class.
    They are taken from https://discord.com/developers/docs/topics/permissions
    """
    def __init__(self, perm_name, perm_num, perm_desc, perm_weight) -> None:
        self.perm_name = perm_name
        self.perm_num = perm_num.split(" ")[0]
        self.perm_desc = perm_desc
        self.perm_weight = int(perm_weight.strip("\n"))
    
    def get_perm_name(self):
        return self.perm_name

    def get_perm_num(self):
        return self.perm_num
    
    def get_perm_desc(self):
        return self.perm_desc

    def get_perm_weight(self):
        return int(self.perm_weight)


class PermissionList():
    """
    This class contains a dictionary of permission objects. 
    """
    def __init__(self) -> None:
        self.permission_list = dict()
    
    def add(self, perm: Permission) -> None:
        self.permission_list[perm.get_perm_num()] = perm

    def get(self, perm_number: str) -> Permission:
        try:
            return self.permission_list[perm_number]
        except KeyError:
            return None
    
    def to_string(self):
        for permission in self.permission_list:
            print(self.permission_list[permission].get_perm_name())


    def string_list(self) -> list():
        """
        Returns a list of all hex permission values.
        """
        results = []
        for item in self.permission_list:
            results.append(item)
        return results


def check_permissions(perm_list: PermissionList, testing_number: int) -> list():
    """
    Take in a hex permission number and converts it into all the relevant permissions.
    """
    results = []
    # If it's equal to -1, it means the bot needs all permissions
    # Not sure why, but it is
    if testing_number < 0:
        for permission in perm_list.permission_list.keys():
            results.append(perm_list.permission_list[permission])
    hex_value = hex(testing_number)
    count = 0
    for char in reversed(hex_value):
        if char.isalpha() and char not in ('a','b', 'c', 'd', 'e', 'f'):
            break
        # This is horrible, but it works, I am sorry
        if char != '0':
            # Add only that character itself.
            if char in ('1','2','4','8'):
                results = add_to_results((int(char),), results, count, perm_list)
            elif char == '3':
                results = add_to_results((1,2), results, count, perm_list)
            elif char == '5':
                results = add_to_results((1,4), results, count, perm_list)
            elif char == '6':
                results = add_to_results((2,4), results, count, perm_list)
            elif char == '7':
                results = add_to_results((1,2,4), results, count, perm_list)
            elif char == '9':
                results = add_to_results((1,8), results, count, perm_list)
            elif char == 'a':
                results = add_to_results((2,8), results, count, perm_list)
            elif char == 'b':
                results = add_to_results((1,2,8), results, count, perm_list)
            elif char == 'c':
                results = add_to_results((4,8), results, count, perm_list)
            elif char == 'd':
                results = add_to_results((1,4,8), results, count, perm_list)
            elif char == 'e':
                results = add_to_results((2,4,8), results, count, perm_list)
            elif char == 'f':
                results = add_to_results((1,2,4,8), results, count, perm_list)
        count += 1
    return results


def add_to_results(list_of_nums:tuple, results:set, count:int, perm_list:PermissionList) -> set:
    """
    Iterates through the list of permissions to convert them into valid hex codes.
    Then adds those permissions to the results set.
    """
    for num in list_of_nums:
        # This nightmare string turns the character into the assoicated permission
        # So it can be easily looked up
        result_hex = f"0x{'0'*(9-int(count))}{num}{('0'*count)}"
        results.append(perm_list.get(result_hex)) 
    return results


def create_permission_list() -> PermissionList:
    """
    Read in the CSV of permissions and create a PermissionList
    """
    perm_dict = PermissionList()

    with open('perms.csv') as f:
        for lines in f.readlines():
            rows = lines.split(",")
            perm = Permission(rows[0], rows[1], rows[2], rows[3])
            perm_dict.add(perm)
    return perm_dict


def compare(a,b):
    if (a.perm_weight == b.perm_weight):
        return 0
    elif (a.perm_weight > b.perm_weight):
        return -1
    else:
        return 1

if __name__ == "__main__":
    check_permissions(create_permission_list(), 2134207679)
