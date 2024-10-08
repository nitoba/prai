import uuid
from typing import Annotated

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition
from typing_extensions import TypedDict

from llm import llm
from pr_tool import pr_tools
from utils import create_tool_node_with_fallback, print_event


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            # configuration = config.get('configurable', {})
            # passenger_id = configuration.get('passenger_id', None)
            # state = {**state, 'user_info': passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get('text')
            ):
                messages = state['messages'] + [
                    ('user', 'Respond with a real output.')
                ]
                state = {**state, 'messages': messages}
            else:
                break
        return {'messages': result}


primary_assistant_prompt = ChatPromptTemplate.from_messages([
    (
        'system',
        'Atue como um desenvolvedor sênior especializado em revisão de código e gerenciamento de versionamento. '
        'Sua tarefa é criar uma descrição de pull request detalhada e precisa para o código que você está revisando. '
        'Você deve usar todas as ferramentas disponíveis para buscar informações relevantes, como commits, diferenças de código, e quaisquer outras anotações pertinentes, para garantir que a descrição forneça uma visão clara e completa das mudanças implementadas.'
        ' Aqui estão as etapas que você deve seguir:',
    ),
    (
        'human',
        '1. **Revise o Código Detalhadamente**: Faça uma análise profunda do código, examinando cada commit, as diferenças (diffs) de código, e qualquer outra informação que possa ajudar a compreender a totalidade das alterações realizadas.\n'
        '2. **Contextualize as Mudanças**: Utilize as mensagens dos commits e outros contextos disponíveis para entender o objetivo das modificações, mas lembre-se de não copiar essas mensagens para a descrição do pull request.\n'
        '3. **Escreva com Clareza e Objetividade**: Redija a descrição de forma clara, concisa e objetiva, destacando apenas informações relevantes e evitando detalhes desnecessários que não agreguem valor ao entendimento do pull request.\n'
        '4. **Formate em Markdown**: A descrição deve ser escrita em formato markdown para garantir legibilidade e organização visual.\n'
        '5. **Redija em Português**: Toda a descrição e o título devem estar em português, respeitando as boas práticas da língua e de escrita técnica.\n'
        '6. **Crie um Título Informativo**: Baseado nas mudanças identificadas, elabore um título preciso e representativo para o pull request, que resuma de forma clara o propósito das modificações realizadas.\n'
        '7. **Falta de Informações**: Caso não haja informações suficientes para formular a descrição de forma completa e precisa, responda com: "Não tenho informações suficientes para responder."\n'
        '\n'
        'Nota: Certifique-se de seguir estas etapas rigorosamente para garantir uma descrição completa, informativa e padronizada. Avalie o código com atenção aos detalhes, garantindo que a descrição final reflita exatamente as alterações implementadas, ajudando assim a equipe a entender e validar as mudanças de forma eficaz.',
    ),
    ('placeholder', '{messages}'),
])

assistant_runnable = primary_assistant_prompt | llm.bind_tools(pr_tools)

graph_builder = StateGraph(State)

# Define nodes: these do the work
graph_builder.add_node('assistant', Assistant(assistant_runnable))
graph_builder.add_node('tools', create_tool_node_with_fallback(pr_tools))

# Define edges: these determine how the control flow moves
graph_builder.add_edge(START, 'assistant')
graph_builder.add_conditional_edges(
    'assistant',
    tools_condition,
)
graph_builder.add_edge('tools', 'assistant')

memory = MemorySaver()

thread_id = str(uuid.uuid4())

graph = graph_builder.compile(checkpointer=memory)


def stream_graph_updates(user_input: str):
    _printed = set()
    events = graph.stream(
        {'messages': ('user', user_input)},
        {'configurable': {'thread_id': thread_id}},
        stream_mode='values',
    )
    for event in events:
        print_event(event, _printed)
        message = event.get('messages')
        if message:
            if isinstance(message, list):
                message = message[-1]
        if isinstance(message, AIMessage) and message.content:
            print('\nAssistant:')
            print(message.content)


stream_graph_updates(
    'Crie uma descrição de pull request da branch: "fix/get-history-links-by-certificadora" para a branch: "sprint/60" no repositório "AGROTRACE-FRONT-V2"'
)
