class Utilities:

    def compare_dict(self, dict1, dict2):
        output = []
        for key1 in dict1:
            if key1 not in dict2:
                output.append(key1)
        return output

    def compare_list(self, list1, list2):
        return list(set(list1)-set(list2))
