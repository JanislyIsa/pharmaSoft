package pe.edu.pe.PharmaBackend.controller;

import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pe.edu.pe.PharmaBackend.dto.PaginaResponseDTO;
import pe.edu.pe.PharmaBackend.dto.VentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.VentaResponseDTO;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.service.service.VentaService;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/ventas")
public class VentaController {
    private static final String CAMPO_ORDENABLE = "fecha";

    private final VentaService ventaService;

    public VentaController(
            VentaService ventaService) {

        this.ventaService = ventaService;
    }

    @PostMapping
    public ResponseEntity<VentaResponseDTO> registrar(
            @Valid
            @RequestBody VentaRequestDTO request) {

        VentaResponseDTO response =
                ventaService.registrar(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    @GetMapping("/buscar")
    public ResponseEntity<PaginaResponseDTO<VentaResponseDTO>> buscarVentas(
            @RequestParam(required = false) Long clienteId,
            @RequestParam(required = false) EstadoVenta estado,
            @RequestParam(required = false) LocalDate desde,
            @RequestParam(required = false) LocalDate hasta,
            @RequestParam(defaultValue = "0") int pagina,
            @RequestParam(defaultValue = "10") int tamanio,
            @RequestParam(defaultValue = "fecha") String ordenarPor,
            @RequestParam(defaultValue = "desc") String direccion) {

        if (pagina < 0 || tamanio < 1) {
            throw new ReglaNegocioException("La página debe ser mayor o igual a 0 y el tamaño mayor a 0.");
        }
        if (desde != null && hasta != null && desde.isAfter(hasta)) {
            throw new ReglaNegocioException("La fecha desde no puede ser posterior a la fecha hasta.");
        }
        if (!CAMPO_ORDENABLE.equals(ordenarPor)) {
            throw new ReglaNegocioException("Campo de orden inválido. Use: fecha.");
        }

        Sort.Direction sentido;
        try {
            sentido = Sort.Direction.fromString(direccion);
        } catch (IllegalArgumentException ex) {
            throw new ReglaNegocioException("Dirección inválida. Use asc o desc.");
        }

        Sort orden = Sort.by(sentido, CAMPO_ORDENABLE).and(Sort.by(sentido, "id"));
        Pageable pageable = PageRequest.of(pagina, tamanio, orden);
        Page<VentaResponseDTO> resultado = ventaService.buscar(clienteId, estado, desde, hasta, pageable);
        return ResponseEntity.ok(new PaginaResponseDTO<>(
                resultado.getContent(),
                resultado.getNumber(),
                resultado.getSize(),
                resultado.getTotalElements(),
                resultado.getTotalPages(),
                resultado.isLast()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<VentaResponseDTO> buscar(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                ventaService.buscar(id)
        );
    }

    @GetMapping
    public ResponseEntity<List<VentaResponseDTO>> listar() {

        return ResponseEntity.ok(
                ventaService.listar()
        );
    }
    @PatchMapping("/{id}/anular")
    public ResponseEntity<VentaResponseDTO> anular(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                ventaService.anular(id)
        );
    }
}
