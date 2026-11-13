package pe.edu.pe.PharmaBackend.controller;
import java.time.LocalDate;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;
import pe.edu.pe.PharmaBackend.dto.*;
import pe.edu.pe.PharmaBackend.service.service.AuditoriaService;
@RestController @RequestMapping("/api/v1/auditoria")
public class AuditoriaController {
 private final AuditoriaService service;
 public AuditoriaController(AuditoriaService service) { this.service=service; }
 @GetMapping public PaginaResponseDTO<AuditoriaEventoDTO> buscar(
  @RequestParam(required=false) String usuario, @RequestParam(required=false) String accion,
  @RequestParam(required=false) @DateTimeFormat(iso=DateTimeFormat.ISO.DATE) LocalDate desde,
  @RequestParam(required=false) @DateTimeFormat(iso=DateTimeFormat.ISO.DATE) LocalDate hasta,
  @RequestParam(defaultValue="0") int pagina, @RequestParam(defaultValue="20") int tamanio) {
  return service.buscar(usuario,accion,desde,hasta,pagina,tamanio);
 }
}
