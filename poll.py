class Poll:

    def __init__(self, item_list: {}, headline: str):
        self.item_list = item_list
        self.headline = headline

        self.item_count = {}
        for item in self.item_list:
            self.item_count[item] = 1

        self.highest_count = 1
        self.highest_item = None

    def add_item(self, new_item):
        for item in self.item_list:
            if item == new_item:
                self.item_count[item] += 1
                if self.item_count[item] > self.highest_count:
                    self.highest_count = self.item_count[item]
                    self.highest_item = item

    def remove_item(self, new_item):
        for item in self.item_list:
            if item == new_item:
                self.item_count[item] -= 1
                # if the current emoji was the most voted, find out the new most voted one
                if self.highest_item == item:
                    highest_item, highest_count = self._get_highest()

                    self.highest_item = highest_item
                    self.highest_count = highest_count

    def _get_highest(self):
        highest_count = 1
        highest_item = None

        for item in self.item_list:
            item_count = self.item_count[item]
            if item_count > highest_count:
                highest_count = item_count
                highest_item = item

        return (highest_item, highest_count)

    def __str__(self):
        poll_string = f"{self.headline} ---> "
        for item in self.item_list:
            poll_string += f"{item}: {self.item_count[item]}, "
        return poll_string[:-2]
