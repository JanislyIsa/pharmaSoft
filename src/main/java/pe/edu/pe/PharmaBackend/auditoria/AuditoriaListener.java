package pe.edu.pe.PharmaBackend.auditoria;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.*;
import pe.edu.pe.PharmaBackend.service.service.AuditoriaService;
@Component
public class AuditoriaListener {
 private static final Logger log=LoggerFactory.getLogger(AuditoriaListener.class);
 private final AuditoriaService service;
 public AuditoriaListener(AuditoriaService service) { this.service=service; }
 @TransactionalEventListener(phase=TransactionPhase.AFTER_COMMIT)
 public void alConfirmar(EventoAuditoria evento) {
  try { service.registrar(evento); }
  catch(RuntimeException ex) { log.error("No se pudo auditar {} {}",evento.accion(),evento.entidadId(),ex); }
 }
}
