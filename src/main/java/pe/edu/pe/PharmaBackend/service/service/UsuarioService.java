package pe.edu.pe.PharmaBackend.service.service;
import pe.edu.pe.PharmaBackend.dto.auth.EmpleadoResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.RolResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.UsuarioRequestDTO;
import pe.edu.pe.PharmaBackend.dto.auth.UsuarioResponseDTO;
import java.util.List;
public interface UsuarioService {
    UsuarioResponseDTO crear(UsuarioRequestDTO request);
    List<UsuarioResponseDTO> listar();
    List<EmpleadoResponseDTO> listarEmpleados();
    List<RolResponseDTO> listarRoles();
}