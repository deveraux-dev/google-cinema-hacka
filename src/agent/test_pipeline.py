import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from agent.pipeline import RevisionPipeline

def test_pipeline():
    original = """
    [Scene 1] INT. WAREHOUSE - DAY
    The warehouse is quiet. John walks in holding a flashlight.
    """
    
    revised = """
    [Scene 1] INT. WAREHOUSE - NIGHT
    The warehouse is dark. John walks in holding a flashlight. 
    Suddenly, a MASSIVE EXPLOSION rocks the building. The structural beams groan and spark.
    John is thrown onto a 15-foot high scaffold.
    """
    
    pipeline = RevisionPipeline()
    result = pipeline.analyze_revision("S1", original, revised)
    
    print("\n=== DIFF ===")
    print(result["diff"].model_dump_json(indent=2))
    
    print("\n=== CASCADE ===")
    print(result["cascade"].model_dump_json(indent=2))
    
    print("\n=== HAZARD TAGS ===")
    print(result["hazard_tags"].model_dump_json(indent=2))

if __name__ == "__main__":
    test_pipeline()
