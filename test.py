from translate import Translator
to_lang = 'ru'
translator = Translator(to_lang=to_lang, from_lang='en')
print(translator.translate('Hello world'))