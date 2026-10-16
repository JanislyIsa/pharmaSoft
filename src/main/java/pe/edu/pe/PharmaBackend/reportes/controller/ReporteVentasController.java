package pe.edu.pe.PharmaBackend.reportes.controller;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.security.access.prepost.PreAuthorize;
import pe.edu.pe.PharmaBackend.reportes.dto.VentaPorCategoriaDTO;
import pe.edu.pe.PharmaBackend.reportes.service.ReporteVentasService;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/reportes")
public class ReporteVentasController {
    private final ReporteVentasService service;

    public ReporteVentasController(ReporteVentasService service) {
        this.service = service;
    }

    @GetMapping("/ventas-por-categoria")
    @PreAuthorize("hasAuthority('REPORTES_VER')")
    public ResponseEntity<List<VentaPorCategoriaDTO>> ventasPorCategoria(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate desde,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate hasta) {
        return ResponseEntity.ok(service.ventasPorCategoria(desde, hasta));
    }
}
