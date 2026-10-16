package pe.edu.pe.PharmaBackend.dto.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class CambiarContrasenaRequestDTO {
    @NotBlank private String contrasenaActual;
    @NotBlank @Size(min = 8, max = 72)
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d).+$", message = "La nueva contraseña debe tener letras y números")
    private String nuevaContrasena;
}
