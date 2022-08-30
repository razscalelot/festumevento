from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from chatterbot import trainers

from chatterbot import response_selection

bot = ChatBot(name='Festum Evento', read_only=True,
              response_selection_method=response_selection.get_random_response,
              trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
              preprocessors=[
                  'chatterbot.preprocessors.clean_whitespace',
                  'chatterbot.preprocessors.convert_to_ascii'
              ],
              logic_adapters=[
                  {
                      'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                      'input_text': 'empty',
                      'output_text': ''
                  },
                  {
                      'import_path': 'chatterbot.logic.BestMatch',
                      'default_response': 'i honestly have no idea how to respond to that',
                      'maximum_similarity_threshold': 0.9
                  },
                  {
                      'import_path': 'chatterbot.logic.MathematicalEvaluation'
                  }, {

                      'import_path': 'chatterbot.logic.TimeLogicAdapter',
                  }

              ]
              )


trainer = ListTrainer(bot)

trainer.train([
    'Good morning, how are you?',
    'I am doing well, how about you?',
    "I'm also good.",
    "That's good to hear.",
    "Yes it is.",
    "Hello",
    "Hi",
    "How are you doing?",
    "I am doing well.",
    "That is good to hear",
    "Yes it is.",
    "Can I help you with anything?",
])
