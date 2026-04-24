from backend.app.models.detector_mode_model import DetectorMode, PRNetOutputMode
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface
from backend.app.services.mediapipe_face_detector import MediaPipeFaceDetector
from backend.app.services.prnet_detector import PRNetFaceDetector


class DetectorFactory:
    @staticmethod
    def create(
        mode: DetectorMode,
        prnet_output_mode: PRNetOutputMode = PRNetOutputMode.LANDMARKS
    ) -> FaceDetectorInterface:
        if mode == DetectorMode.MEDIAPIPE:
            return MediaPipeFaceDetector()

        if mode == DetectorMode.PRNET:
            return PRNetFaceDetector(output_mode=prnet_output_mode.value)

        raise ValueError(f"Modo de detector no soportado: {mode}")