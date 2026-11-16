package pe.edu.pe.PharmaBackend.auditoria;
import org.slf4j.MDC;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
public record EventoAuditoria(String usuario, String accion, String entidad, Long entidadId,
                              String detalle, String requestId) {
 public static String usuarioActual(String defecto) {
  var a = SecurityContextHolder.getContext().getAuthentication();
  return a == null || !a.isAuthenticated() || a instanceof AnonymousAuthenticationToken
   ? defecto : recortar(a.getName(), 50);
 }
 public static EventoAuditoria de(String accion, String entidad, Long id, String detalle) {
  return new EventoAuditoria(usuarioActual("anonimo"), accion, entidad, id,
   recortar(detalle, 500), MDC.get("requestId"));
 }
 public static EventoAuditoria login(String accion, String usuario) {
  return new EventoAuditoria(recortar(usuario,50), accion, "Usuario", null, null, MDC.get("requestId"));
 }
 private static String recortar(String texto, int max) {
  return texto == null || texto.length() <= max ? texto : texto.substring(0,max);
 }
}
