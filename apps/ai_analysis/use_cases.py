from apps.ai_analysis.client import AiVisionClient
from apps.ai_analysis.parser import AiAttributeParser
from apps.ai_analysis.repositories import SubjectiveAttributeRepository


class AnalyzePhotoUseCase:
    def __init__(self, client=None):
        self.client = client or AiVisionClient()

    def execute(self, photo, prompt):
        if not prompt:
            return []
        response = self.client.analyze_photo(photo, prompt)
        attributes = AiAttributeParser.extract_attributes(response)
        SubjectiveAttributeRepository.replace_photo_attributes(photo, attributes)
        return attributes


class AnalyzePropertyUseCase:
    def __init__(self, analyze_photo_use_case=None):
        self.analyze_photo_use_case = analyze_photo_use_case or AnalyzePhotoUseCase()

    def execute(self, property_obj, prompt):
        results = []
        for photo in property_obj.photos.all():
            attributes = self.analyze_photo_use_case.execute(photo, prompt)
            results.append({"photo_id": photo.id, "attributes": attributes})
        return results
