package pe.edu.pe.PharmaBackend.controller;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import pe.edu.pe.PharmaBackend.dto.ProductoRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ProductoResponseDTO;
import pe.edu.pe.PharmaBackend.service.service.CategoriaService;
import pe.edu.pe.PharmaBackend.service.service.ProductoService;

@RestController
@RequestMapping("/api/v1/productos")
public class ProductoController {
    private final CategoriaService categoriaService;
    private final ProductoService productoService;

    public ProductoController(ProductoService productoService, CategoriaService categoriaService) {
        this.categoriaService = categoriaService;
        this.productoService = productoService;
    }

    @GetMapping
    public ResponseEntity<Iterable<ProductoResponseDTO>> findAll(){
        return ResponseEntity.ok(
                productoService.readAll()
        );
    }
    @GetMapping("/{id}")
    public ResponseEntity<ProductoResponseDTO> findById(@PathVariable Long id){
        ResponseEntity.ok(productoService.read(id));
        return null;
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