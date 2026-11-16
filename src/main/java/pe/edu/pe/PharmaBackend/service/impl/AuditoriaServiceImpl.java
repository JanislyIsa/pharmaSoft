package pe.edu.pe.PharmaBackend.service.impl;
import java.time.LocalDate;
import java.time.LocalDateTime;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.*;
import pe.edu.pe.PharmaBackend.auditoria.EventoAuditoria;
import pe.edu.pe.PharmaBackend.dto.*;
import pe.edu.pe.PharmaBackend.entity.AuditoriaEvento;
import pe.edu.pe.PharmaBackend.repository.AuditoriaEventoRepository;
import pe.edu.pe.PharmaBackend.service.service.AuditoriaService;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
@Service
public class AuditoriaServiceImpl implements AuditoriaService {
 private final AuditoriaEventoRepository repository;
 public AuditoriaServiceImpl(AuditoriaEventoRepository repository) { this.repository=repository; }
 @Override @Transactional(propagation=Propagation.REQUIRES_NEW)
 public void registrar(EventoAuditoria e) {
  var a=new AuditoriaEvento(); a.setFecha(LocalDateTime.now()); a.setUsuario(e.usuario());
  a.setAccion(e.accion()); a.setEntidad(e.entidad()); a.setEntidadId(e.entidadId());
  a.setDetalle(e.detalle()); a.setRequestId(e.requestId()); repository.save(a);
 }
 @Override @Transactional(readOnly=true)
 public PaginaResponseDTO<AuditoriaEventoDTO> buscar(String usuario,String accion,LocalDate desde,
   LocalDate hasta,int pagina,int tamanio) {
  if (pagina<0 || tamanio<1 || tamanio>100) throw new ReglaNegocioException("Página o tamaño inválidos (1 a 100).");
  if (desde!=null && hasta!=null && desde.isAfter(hasta)) throw new ReglaNegocioException("El rango de fechas es inválido.");
  var p=repository.buscar(limpiar(usuario),limpiar(accion),desde==null?null:desde.atStartOfDay(),
   hasta==null?null:hasta.plusDays(1).atStartOfDay(),
   PageRequest.of(pagina,tamanio,Sort.by(Sort.Direction.DESC,"fecha","id"))).map(AuditoriaEventoDTO::de);
  return new PaginaResponseDTO<>(p.getContent(),p.getNumber(),p.getSize(),p.getTotalElements(),p.getTotalPages(),p.isLast());
 }
 private String limpiar(String s) { return s==null || s.isBlank()?null:s.trim(); }
}
