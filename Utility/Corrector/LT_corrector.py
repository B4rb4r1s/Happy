import language_tool_python
import tqdm
import config


class LT_corrector:
    def __init__(self):
        pass
        # self.good_rules = [
            # rule.ruleId != 'MORFOLOGIK_RULE_RU_RU' and \
            # rule.ruleId != 'UPPERCASE_SENTENCE_START' and \
            # rule.ruleId != 'Cap_Letters_Name' and \
        # ]


    # /root/.cache/language_tool_python
    def run_LT(self, text):
        # [rule.ruleId != f'{rule}' for rule in self.good_rules]
        is_good_rule = lambda rule: \
            rule.ruleId != 'MORFOLOGIK_RULE_RU_RU' and \
            rule.ruleId != 'UPPERCASE_SENTENCE_START' and \
            rule.ruleId != 'Cap_Letters_Name' and \
            len(rule.replacements) and \
            rule.replacements[0][0].isupper()

        # dataset = get_table('language_tool')
        if text: 
            dataset = [text]
        tool = language_tool_python.LanguageTool('auto')

        array_matches = []
        for text in tqdm.tqdm(dataset):
            try:
                matches = tool.check(config.PROCESSING_HANDLER(text))
                # matches = [rule for rule in matches if is_good_rule(rule)]
                for i, match in enumerate(matches):
                    # yield i, match
                    print(i, match)
                    array_matches.append(match)
            except Exception as err:
                print(f'[ ERROR ] >>> {err}')
                continue
        return array_matches


if __name__ == '__main__':
    lt = LT_corrector()
    text = '''
	3) формирование, знаний об опертивно-тактической обстановке;
	4) автоматическое распро странение бообщенной информации? об оперативно-тактической обстановке;'''
    lt.run_LT(text)