import math
from permissions import PermissionList, check_permissions
from permissions import check_permissions, create_permission_list

class Bot():
    def __init__(self) -> None:
        self.permissions_list = create_permission_list()
        self.permissions = create_permission_list()
        self.permissions_score = []  
        self.final_score = 0
        self.verified = False
        self.source_code = False
        
        self.website = ""
        self.image = ""
        self.prefix = ""

        # Any warnings that might affect the data
        self.warnings = []
        # Errors that caused the bot not to calculate a score
        self.error = ""

        self.server_count = []
        self.user_count = []
        self.review_score = []
        self.review_count = []
        self.invite_count = []
        

    def get_permission_dict(self) -> None:
        return self.permissions_list

    def get_permission_list(self) -> None:
        return self.permissions

    def calculate_score(self) -> int:
        """
        Take in all data gathered by web scrapers and generate the bots score.
        """
        final_score = 0
        sub_score = 0
        
         # Permissions #
        final_score += (sum(self.permissions_score)/len(self.permissions_score))

        # Review Score && Number of Reviews #
        normalized_review_count = self.normalize_this(self.review_count)
        if normalized_review_count != 0:
            average_review_count = normalized_review_count/len(self.review_count)
            final_review_score = math.floor(math.log10(average_review_count))
            # The review score is multiplied by the scale of the number of reviews
            # This is then subtracted from the final score 
            final_score -= (sum(self.review_score)/20)/len(self.review_score) * final_review_score

        # Website Check #
        if self.website != "":
            final_score -= 15 
        
        # Server Count #
        sub_score = self.normalize_this(self.server_count)
        if sub_score != 0:
            sub_score = sub_score/len(self.server_count)
            final_score -= math.floor(math.log10(sub_score)) * 2

        # User Count # 
        sub_score = self.normalize_this(self.user_count)
        if sub_score != 0:
            sub_score = sub_score/len(self.user_count)
            final_score -= math.floor(math.log10(sub_score)) 
     
        if final_score < 0:
            final_score = 0
        elif final_score > 100:
            final_score = 100
        self.final_score = final_score


    def normalize_this(self, value_list:list) -> int:
        """
        Takes in a number like 123k or 1.2m and converts them into
        123,000 or 1,200,000 respectively (as ints, i.e. without commas)
        """
        result = 0 
        for value in value_list:
            # Most websites abbreviate 1,000 as 1k, so it must be converted
            if type(value) != int:  
                if value[-1] == "k":
                    result = int(value[:-1])*1000
                elif value[-1] == "m":
                    result += int(value[:-1])*1000000 
            else:
                result += value
        return result


    def load_permissions(self, permission_number:int, permission_list_instance:PermissionList) -> None:
        """
        Calculates the permissions a bot should have and also the weight of the permissions.
        """
        tmp = 0
        self.permissions = check_permissions(permission_list_instance, permission_number)
        for permission in self.permissions:
            tmp += permission.get_perm_weight()
        self.permissions_score.append(tmp)
   