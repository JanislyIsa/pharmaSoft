package pe.edu.pe.PharmaBackend.dto;
import java.time.LocalDateTime;
import pe.edu.pe.PharmaBackend.entity.AuditoriaEvento;
public record AuditoriaEventoDTO(Long id, LocalDateTime fecha, String usuario, String accion,
 String entidad, Long entidadId, String detalle, String requestId) {
 public static AuditoriaEventoDTO de(AuditoriaEvento a) {
  return new AuditoriaEventoDTO(a.getId(),a.getFecha(),a.getUsuario(),a.getAccion(),
   a.getEntidad(),a.getEntidadId(),a.getDetalle(),a.getRequestId());
 }
}
