package pe.edu.pe.PharmaBackend.controller;

import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pe.edu.pe.PharmaBackend.dto.PaginaResponseDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoResponseDTO;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.service.service.ProductoService;

import java.util.Set;

@RestController
@RequestMapping("/api/v1/productos")
public class ProductoController {
    private static final Set<String> CAMPOS_ORDENABLES = Set.of("id", "nombre", "precio", "stock");
    private final ProductoService productoService;

    public ProductoController(ProductoService productoService) {
        this.productoService = productoService;
    }

    @GetMapping
    public ResponseEntity<PaginaResponseDTO<ProductoResponseDTO>> findAll(
            @RequestParam(defaultValue = "0") int pagina,
            @RequestParam(defaultValue = "20") int tamanio,
            @RequestParam(defaultValue = "nombre") String ordenarPor,
            @RequestParam(defaultValue = "asc") String direccion) {

        if (pagina < 0 || tamanio < 1 || tamanio > 100) {
            throw new ReglaNegocioException("La página debe ser mayor o igual a 0 y el tamaño estar entre 1 y 100.");
        }
        if (!CAMPOS_ORDENABLES.contains(ordenarPor)) {
            throw new ReglaNegocioException("Campo de orden inválido. Use: id, nombre, precio o stock.");
        }

        Sort.Direction sentido;
        try {
            sentido = Sort.Direction.fromString(direccion);
        } catch (IllegalArgumentException ex) {
            throw new ReglaNegocioException("Dirección inválida. Use asc o desc.");
        }

        Sort orden = Sort.by(sentido, ordenarPor).and(Sort.by(sentido, "id"));
        Pageable pageable = PageRequest.of(pagina, tamanio, orden);
        return ResponseEntity.ok(productoService.listar(pageable));
    }
    @GetMapping("/buscar")
    public PaginaResponseDTO<ProductoResponseDTO> buscarVendibles(@RequestParam(defaultValue="") String texto) {
        if (texto.length()>150) throw new ReglaNegocioException("La búsqueda admite hasta 150 caracteres.");
        return productoService.buscarVendibles(texto.trim(), PageRequest.of(0,20,Sort.by("nombre","id")));
    }
    @GetMapping("/{id}")
    public ResponseEntity<ProductoResponseDTO> findById(@PathVariable Long id){
        return ResponseEntity.ok(productoService.read(id));
    }
    @PostMapping
    public ResponseEntity<ProductoResponseDTO> create(@Valid @RequestBody ProductoRequestDTO requestDTO){
        ProductoResponseDTO response = productoService.create(requestDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProductoResponseDTO> update(
            @PathVariable Long id,
            @Valid @RequestBody ProductoRequestDTO requestDTO) {

        ProductoResponseDTO response = productoService.update(id, requestDTO);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ProductoResponseDTO> delete(
            @PathVariable Long id){
        productoService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
