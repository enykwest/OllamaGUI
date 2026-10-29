'''
Currently a debugging tool, but could evolve into a high level replacement.
'''
# Disable crewai telemetry
# Set environment flags BEFORE importing crewai
import os
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

from typing import Any, Dict, List
from crewai import Agent

# Custom Agent for debugging
class CustomAgent(Agent):

    '''
    def _prepare_kickoff(
    self,
    messages: str | list[Any],
    response_format: type[Any] | None = None,
    input_files: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any], dict[str, Any], list[Any]]:
        print(messages, response_format, input_files,)
    '''

    def __kickoff(self, **kwargs):
        return super().kickoff(**kwargs)
    
    def kickoff(
    self,
    messages: str | list[Any],
    response_format: type[Any] | None = None,
    input_files: dict[str, Any] | None = None,
    from_checkpoint: Any | None = None,
    ) -> Any | Any:
        # Debugging
        print('Input to kickoff: ' , messages, response_format, input_files , from_checkpoint, '\n')

        executor, inputs, agent_info, parsed_tools = self._prepare_kickoff(
                messages, response_format, input_files
            )

        print('Agent properties')
        print('\n' , self.use_system_prompt, "|", self.system_template, "|", self.prompt_template, "|", self.response_template,)

        print('\n executor build')
        for item in self._build_execution_prompt([]):
            print(type(item), item, '\n---')
        
        print('Output from prepare kickoff:\n')
        for item in [executor, inputs, agent_info, parsed_tools ]:
            print(item, '\n---')


        # overload self._build_execution_prompt
        #def _build_execution_prompt(self, raw_tools):
        #    prompt, stop_words, rpm_limit_fn = super()._build_execution_prompt(raw_tools)

        response = self.__kickoff(messages=messages, response_format=response_format, input_files=input_files , from_checkpoint=from_checkpoint)
        print(response)
        return response
        
    