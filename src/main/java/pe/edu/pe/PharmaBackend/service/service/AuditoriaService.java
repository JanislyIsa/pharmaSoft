package pe.edu.pe.PharmaBackend.service.service;
import java.time.LocalDate;
import pe.edu.pe.PharmaBackend.auditoria.EventoAuditoria;
import pe.edu.pe.PharmaBackend.dto.*;
public interface AuditoriaService {
 void registrar(EventoAuditoria evento);
 PaginaResponseDTO<AuditoriaEventoDTO> buscar(String usuario,String accion,LocalDate desde,
   LocalDate hasta,int pagina,int tamanio);
}
