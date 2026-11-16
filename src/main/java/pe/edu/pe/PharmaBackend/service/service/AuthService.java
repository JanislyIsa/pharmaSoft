package pe.edu.pe.PharmaBackend.service.service;

import pe.edu.pe.PharmaBackend.dto.auth.LoginRequestDTO;
import pe.edu.pe.PharmaBackend.dto.auth.LoginResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.UsuarioResponseDTO;
import pe.edu.pe.PharmaBackend.dto.auth.CambioPasswordRequestDTO;
public interface AuthService {
    LoginResponseDTO login(LoginRequestDTO request);
    UsuarioResponseDTO usuarioActual(String username);
    void cambiarPassword(String username, CambioPasswordRequestDTO request);
}
