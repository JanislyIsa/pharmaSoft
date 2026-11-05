package pe.edu.pe.PharmaBackend.dto.auth;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CambiarEstadoUsuarioRequestDTO {
    @NotNull(message = "El estado es obligatorio")
    private Boolean estado;
}
