package pe.edu.pe.PharmaBackend.controller;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;
import pe.edu.pe.PharmaBackend.dto.ClienteRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ClienteResponseDTO;
import pe.edu.pe.PharmaBackend.dto.PaginaResponseDTO;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.service.service.ClienteService;

import java.util.Set;

@RestController
@RequestMapping("/api/v1/clientes")
public class ClienteController {

    private static final Set<String> CAMPOS_ORDENABLES =
            Set.of("id", "dni", "nombres", "apellidos", "email");

    private final ClienteService clienteService;

    public ClienteController(
            ClienteService clienteService) {

        this.clienteService = clienteService;
    }

    @PostMapping
    public ResponseEntity<ClienteResponseDTO> create(
            @Valid
            @RequestBody ClienteRequestDTO request) {

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(clienteService.create(request));
    }

    @GetMapping
    public ResponseEntity<PaginaResponseDTO<ClienteResponseDTO>> readAll(
            @RequestParam(defaultValue = "0") int pagina,
            @RequestParam(defaultValue = "10") int tamanio,
            @RequestParam(defaultValue = "apellidos") String ordenarPor,
            @RequestParam(defaultValue = "asc") String direccion) {

        if (pagina < 0 || tamanio < 1) {
            throw new ReglaNegocioException(
                    "La página debe ser mayor o igual a 0 y el tamaño mayor a 0."
            );
        }
        if (!CAMPOS_ORDENABLES.contains(ordenarPor)) {
            throw new ReglaNegocioException(
                    "Campo de orden inválido. Use: id, dni, nombres, apellidos o email."
            );
        }

        Sort.Direction sentido;
        try {
            sentido = Sort.Direction.fromString(direccion);
        } catch (IllegalArgumentException ex) {
            throw new ReglaNegocioException(
                    "Dirección inválida. Use asc o desc."
            );
        }

        Pageable pageable = PageRequest.of(
                pagina,
                tamanio,
                Sort.by(sentido, ordenarPor)
        );
        return ResponseEntity.ok(clienteService.listar(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ClienteResponseDTO> read(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                clienteService.read(id)
        );
    }

    @PutMapping("/{id}")
    public ResponseEntity<ClienteResponseDTO> update(
            @PathVariable Long id,
            @Valid
            @RequestBody ClienteRequestDTO request) {

        return ResponseEntity.ok(
                clienteService.update(id, request)
        );
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @PathVariable Long id) {

        clienteService.delete(id);

        return ResponseEntity
                .noContent()
                .build();
    }
}
