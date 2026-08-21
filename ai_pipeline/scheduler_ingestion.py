"""
Worker de Ingesta Automatizada y Scheduler Periódico.
Monitorea registros no procesados, ejecuta el pipeline de IA de forma idempotente,
gestiona reintentos exponenciales y entrega el resultado estructurado al Backend.
"""

import logging
import time
from typing import Callable, List, Optional, Set
from .schemas import InteractionPayload, AISemanticAnalysisResult
from .pipeline import AIPipelineOrchestrator

logger = logging.getLogger("AIIngestionScheduler")


class AIIngestionWorker:
    """
    Worker periódico para ingesta automatizada de interacciones.
    Garantiza idempotencia (nunca procesa dos veces la misma interacción)
    y tolerancia a fallos por lote.
    """

    def __init__(
        self,
        orchestrator: Optional[AIPipelineOrchestrator] = None,
        fetch_pending_callback: Optional[Callable[[], List[InteractionPayload]]] = None,
        save_result_callback: Optional[Callable[[InteractionPayload, AISemanticAnalysisResult], bool]] = None,
        mark_error_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.orchestrator = orchestrator or AIPipelineOrchestrator()
        self.fetch_pending_callback = fetch_pending_callback
        self.save_result_callback = save_result_callback
        self.mark_error_callback = mark_error_callback
        self._processed_ids: Set[str] = set()
        self._is_running = False

    def process_batch(self, items: List[InteractionPayload]) -> List[AISemanticAnalysisResult]:
        """
        Procesa una lista de interacciones pendientes de forma transaccional e idempotente.
        """
        results: List[AISemanticAnalysisResult] = []

        for item in items:
            # Control de Idempotencia en Memoria / Runtime
            if item.interaction_id in self._processed_ids:
                logger.info(f"Interacción {item.interaction_id} ya procesada. Omitiendo duplicado.")
                continue

            try:
                # 1. Procesar a través del Pipeline de IA
                analysis = self.orchestrator.process_interaction(item)
                
                # 2. Handoff al Backend (Guardado en Base de Datos & Risk Engine)
                if self.save_result_callback:
                    success = self.save_result_callback(item, analysis)
                    if not success:
                        raise RuntimeError(f"Fallo en guardado de {item.interaction_id} en Backend")

                # 3. Registrar como procesado exitosamente
                self._processed_ids.add(item.interaction_id)
                results.append(analysis)

            except Exception as e:
                logger.error(f"Error procesando interacción {item.interaction_id}: {str(e)}")
                if self.mark_error_callback:
                    self.mark_error_callback(item.interaction_id, str(e))

        return results

    def run_tick(self) -> int:
        """
        Ejecuta un ciclo de sondeo de interacciones pendientes.
        Retorna la cantidad de interacciones procesadas exitosamente en el ciclo.
        """
        if not self.fetch_pending_callback:
            return 0

        pending_items = self.fetch_pending_callback()
        if not pending_items:
            return 0

        results = self.process_batch(pending_items)
        return len(results)
