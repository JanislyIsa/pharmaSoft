package pe.edu.pe.PharmaBackend.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.List;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger LOG = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(RecursoNoEncontradoException.class)
    public ResponseEntity<ErrorResponseDTO> handleRecursoNoEncontrado(RecursoNoEncontradoException ex, WebRequest request) {
        LOG.warn("Recurso no encontrado: {}", ex.getMessage());
        return construir(HttpStatus.NOT_FOUND, ex.getMessage(), request, null);
    }

    @ExceptionHandler(ReglaNegocioException.class)
    public ResponseEntity<ErrorResponseDTO> handleReglaNegocio(ReglaNegocioException ex, WebRequest request) {
        LOG.warn("Regla de negocio violada: {}", ex.getMessage());
        return construir(HttpStatus.CONFLICT, ex.getMessage(), request, null);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDTO> handleValidacion(MethodArgumentNotValidException ex, WebRequest request) {
        List<String> detalles = ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .toList();
        LOG.warn("Error de validación: {}", detalles);
        return construir(HttpStatus.BAD_REQUEST, "Datos de entrada inválidos", request, detalles);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponseDTO> handleGeneral(Exception ex, WebRequest request) {
        LOG.error("Error no controlado: {}", ex.getMessage(), ex);
        return construir(HttpStatus.INTERNAL_SERVER_ERROR, "Ocurrió un error interno en el servidor", request, null);
    }

    private ResponseEntity<ErrorResponseDTO> construir(HttpStatus status, String mensaje, WebRequest request, List<String> detalles) {
        ErrorResponseDTO error = new ErrorResponseDTO(
                LocalDateTime.now(), status.value(), status.getReasonPhrase(),
                mensaje, request.getDescription(false).replace("uri=", ""), detalles);
        return ResponseEntity.status(status).body(error);
    }
}