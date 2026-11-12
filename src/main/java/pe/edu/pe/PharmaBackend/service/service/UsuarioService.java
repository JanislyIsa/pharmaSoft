package pe.edu.pe.PharmaBackend.service.service;
import pe.edu.pe.PharmaBackend.dto.auth.EmpleadoResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.RolResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.UsuarioRequestDTO;
import pe.edu.pe.PharmaBackend.dto.auth.UsuarioResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.AsignarRolesRequestDTO;
import pe.edu.pe.PharmaBackend.dto.auth.CambiarEstadoUsuarioRequestDTO;
import java.util.List;
public interface UsuarioService {
    UsuarioResponseDTO crear(UsuarioRequestDTO request);
    List<UsuarioResponseDTO> listar();
    List<EmpleadoResponseDTO> listarEmpleados();
    List<RolResponseDTO> listarRoles();
    UsuarioResponseDTO asignarRoles(Long id, AsignarRolesRequestDTO request, String actor);
    UsuarioResponseDTO cambiarEstado(Long id, CambiarEstadoUsuarioRequestDTO request, String actor);
}
