from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class ExperimentContext:
    DATA_HOME: Path ## this is the type that DATA_HOME has, type annotations

    def get_webcam_storage_path(self, palette: str, set_letter: str, distance: str, room:str):
        return self.DATA_HOME / palette / set_letter / distance / room 


@dataclass
class ExperimentConfig:
    
    pipelist:list[PipelineStep]

## classes are objects?
    @classmethod
    def from_json(cls, path_config_file):
        '''
        Takes in a json file 
        Turn it into a dictionary
        Return the dictionary?
        '''
        with open(path_config_file) as f:
            pipeline_list = json.load(f) ## returns a dictionary
            pipeline = [eval(x["type"])(**x) for x in pipeline_list]
        return pipeline    

