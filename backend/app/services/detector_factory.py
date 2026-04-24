from backend.app.models.detector_mode_model import DetectorMode
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface
from backend.app.services.mediapipe_face_detector import MediaPipeFaceDetector
from backend.app.services.prnet_detector import PRNetFaceDetector


class DetectorFactory:
    @staticmethod
    def create(mode: DetectorMode) -> FaceDetectorInterface:
        if mode == DetectorMode.MEDIAPIPE:
            return MediaPipeFaceDetector()

        if mode == DetectorMode.PRNET:
            return PRNetFaceDetector()

        raise ValueError(f"Modo de detector no soportado: {mode}")