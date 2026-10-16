package pe.edu.pe.PharmaBackend.reportes.service;

import org.springframework.stereotype.Service;
import pe.edu.pe.PharmaBackend.exception.ReglaNegocioException;
import pe.edu.pe.PharmaBackend.reportes.dto.VentaPorCategoriaDTO;
import pe.edu.pe.PharmaBackend.reportes.repository.ReporteVentasRepository;

import java.time.LocalDate;
import java.util.List;

@Service
public class ReporteVentasService {
    private final ReporteVentasRepository repository;

    public ReporteVentasService(ReporteVentasRepository repository) {
        this.repository = repository;
    }

    public List<VentaPorCategoriaDTO> ventasPorCategoria(LocalDate desde, LocalDate hasta) {
        if (desde != null && hasta != null && desde.isAfter(hasta)) {
            throw new ReglaNegocioException("La fecha desde no puede ser posterior a la fecha hasta.");
        }

        return repository.ventasPorCategoria(
                        desde == null ? null : desde.atStartOfDay(),
                        hasta == null ? null : hasta.plusDays(1).atStartOfDay())
                .stream()
                .map(row -> new VentaPorCategoriaDTO(
                        row.getCategoriaId(),
                        row.getCategoriaNombre(),
                        row.getCantidadVendida(),
                        row.getMontoTotal()))
                .toList();
    }
}
