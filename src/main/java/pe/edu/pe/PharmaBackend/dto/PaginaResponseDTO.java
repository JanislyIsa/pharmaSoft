package pe.edu.pe.PharmaBackend.dto;

import java.io.Serializable;
import java.util.List;

public record PaginaResponseDTO<T>(
        List<T> contenido,
        int pagina,
        int tamanio,
        long totalElementos,
        int totalPaginas,
        boolean ultima
) implements Serializable {
    private static final long serialVersionUID = 1L;
}
