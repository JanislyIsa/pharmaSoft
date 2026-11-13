package pe.edu.pe.PharmaBackend.auditoria;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.*;
import org.slf4j.MDC;
import org.springframework.security.authentication.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import pe.edu.pe.PharmaBackend.config.AuditoriaConfig;
import pe.edu.pe.PharmaBackend.repository.AuditoriaEventoRepository;
import pe.edu.pe.PharmaBackend.service.impl.AuditoriaServiceImpl;
import pe.edu.pe.PharmaBackend.service.service.AuditoriaService;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
class AuditoriaTest {
 @AfterEach void limpiar() { SecurityContextHolder.clearContext(); MDC.clear(); }
 @Test void auditorUsaSistemaParaAnonimoYNombreParaAutenticado() {
  var auditor=new AuditoriaConfig().auditor(); assertEquals("sistema",auditor.getCurrentAuditor().orElseThrow());
  SecurityContextHolder.getContext().setAuthentication(new AnonymousAuthenticationToken("key","anonymous",List.of(new SimpleGrantedAuthority("ROLE_ANONYMOUS"))));
  assertEquals("sistema",auditor.getCurrentAuditor().orElseThrow());
  SecurityContextHolder.getContext().setAuthentication(new UsernamePasswordAuthenticationToken("vendedor",null,List.of(new SimpleGrantedAuthority("VENTAS_REGISTRAR"))));
  assertEquals("vendedor",auditor.getCurrentAuditor().orElseThrow());
 }
 @Test void eventoConservaCorrelacionYRecortaSinGuardarCredenciales() {
  MDC.put("requestId","abc123");var e=EventoAuditoria.de("VENTA_REGISTRADA","Venta",1L,"x".repeat(600));
  assertEquals(500,e.detalle().length());assertEquals("abc123",e.requestId());
  assertNull(EventoAuditoria.login("LOGIN_FALLIDO","u".repeat(80)).detalle());
  assertEquals(50,EventoAuditoria.login("LOGIN_FALLIDO","u".repeat(80)).usuario().length());
 }
 @Test void consultaInvalidaNoAccedeAlRepositorio() {
  var repo=mock(AuditoriaEventoRepository.class);var servicio=new AuditoriaServiceImpl(repo);
  assertThrows(ReglaNegocioException.class,()->servicio.buscar(null,null,null,null,0,500));
  assertThrows(ReglaNegocioException.class,()->servicio.buscar(null,null,LocalDate.of(2026,11,13),LocalDate.of(2026,11,1),0,20));
  verifyNoInteractions(repo);
 }
 @Test void falloDeAuditoriaNoConvierteEnErrorUnCommitConfirmado() {
  var servicio=mock(AuditoriaService.class);var evento=EventoAuditoria.de("VENTA_REGISTRADA","Venta",1L,null);
  doThrow(new RuntimeException("fallo de almacenamiento simulado")).when(servicio).registrar(evento);
  assertDoesNotThrow(()->new AuditoriaListener(servicio).alConfirmar(evento));
 }
}
