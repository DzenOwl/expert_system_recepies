import itertools


class Recipes(object):
    def __init__(self, facts, rules):
        self.facts = facts
        self.last_key_fact = sorted(list(self.facts.keys()))[-1]
        
        self.rules = rules
        self.last_key_rules = sorted(list(self.rules.keys()))[-1]
        
        self.background_facts = set()
        
        self.avail_facts = self.background_facts.copy()

        self.dict_search = {}

    def get_number_fact(self, name_fact):
        return list(self.facts.keys())[list(self.facts.values()).index(name_fact)]

    def is_fact(self, name_fact):
        return name_fact in self.facts.values()

    def add_fact(self, name_fact):
        if not self.is_fact(name_fact):
            self.last_key_fact += 1
            self.facts[self.last_key_fact] = name_fact
        else:
            print("Данный факт уже существует")

    def add_rule(self, name_fact):
        if self.is_fact(name_fact):
            rule_facts = set()
            while True:
                print("1. добавить отдельный факт")
                print("2. добавить перечисление фактов")
                print("3. закончить")
                ans1 = input("Выбор: ")

                if ans1 == "1":
                    fact = input("факт: ")
                    if self.is_fact(fact):
                        rule_facts.add(self.get_number_fact(fact))
                    else:
                        print("Такого факта не существует")
                elif ans1 == "2":
                    or_facts = set()
                    while True:
                        print("1. добавить отдельный факт")
                        print("2. закончить")
                        ans2 = input("Выбор: ")

                        if ans2 == "1":
                            fact = input("факт: ")
                            if self.is_fact(fact):
                                or_facts.add(self.get_number_fact(fact))
                            else:
                                print("Такого факта не существует")
                        elif ans2 == "2":
                            rule_facts.add(tuple(or_facts))
                            break
                        else:
                            print("Неверный ввод!")
                elif ans1 == "3":
                    self.last_key_rules += 1
                    self.rules[self.last_key_rules] = [self.get_number_fact(name_fact), rule_facts]
                    break
                else:
                    print("Неверный ввод!")

        else:
            print("Такого факта не существует")

    def get_record_rules(self):
        list_record_rules = []
        for key, val in self.rules.items():
            ingrs = val[1]
            ingrs_text = []
            for fact in ingrs:
                if not isinstance(fact, tuple):
                    ingrs_text.append(self.facts[fact])
                else:
                    or_facts_text = [self.facts[or_fact] for or_fact in fact]
                    ingrs_text.append('(' + "||".join(or_facts_text) + ')')

            list_record_rules.append(f"П{key}: {'&'.join(ingrs_text)} -> {self.facts[val[0]]}")

        return list_record_rules

    
    def set_background_facts(self, set_facts):
        self.background_facts = set_facts
        self.avail_facts = self.background_facts.copy()

    
    def find_all_avail_facts(self):
        archive = []
        memory = []

        def fact_search_text(fact):
            def individ_fact_search_text(ind_f):
                if ind_f in self.dict_search:
                    return self.dict_search[ind_f]
                else:
                    return self.facts[ind_f]

            if not isinstance(fact, tuple):
                return individ_fact_search_text(fact)
            ind_facts = []
            for ind_fact in fact:
                ind_facts.append(individ_fact_search_text(ind_fact))
            return '(' + "||".join(ind_facts) + ')'

        def expand_rule(ingrs):
            tuple_facts = []
            ingrs_copy = ingrs.copy()
            ingrs_exp = []

            for ingr in ingrs:
                if isinstance(ingr, tuple):
                    tuple_facts.append(ingr)
                    ingrs_copy.remove(ingr)

            for part_rule in itertools.product(*tuple_facts):
                ingrs_exp.append(ingrs_copy | set(part_rule))

            return ingrs_exp

        def is_possible(ingrs_orig, avail_facts):
            if all(not isinstance(fact, tuple) for fact in ingrs_orig):
                return len(ingrs_orig - avail_facts) == 0
            ingrs_exp = expand_rule(ingrs_orig)
            for ingrs in ingrs_exp:
                if len(ingrs - avail_facts) == 0:
                    return True
            return False

        while True:
            for rul_num, rul in self.rules.items():
                
                if rul_num not in archive and is_possible(rul[1], self.avail_facts):
                    
                    memory.append(rul_num)
                    archive.append(rul_num)
            
            if len(memory) == 0:
                break

            for rul_num in memory:
                
                fact_num = self.rules[rul_num][0]
                self.avail_facts.add(fact_num)

                
                ingredients = self.rules[rul_num][1]
                ingredients_text = list(map(fact_search_text, ingredients))
                self.dict_search[fact_num] = f"{self.facts[fact_num]}[П{rul_num}:{'&'.join(ingredients_text)}]"

            memory = []

    def get_background_facts(self):
        return [self.facts[fact] for fact in self.background_facts]
    
    def get_new_facts(self):
        self.find_all_avail_facts()
        return [self.facts[fact] for fact in self.avail_facts - self.background_facts]
    
    def get_records_how_new_facts_was_received(self):
        return self.dict_search
