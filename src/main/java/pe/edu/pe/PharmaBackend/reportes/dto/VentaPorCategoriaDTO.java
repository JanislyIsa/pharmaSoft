package pe.edu.pe.PharmaBackend.reportes.dto;

import java.math.BigDecimal;

public record VentaPorCategoriaDTO(
        Long categoriaId,
        String categoriaNombre,
        Long cantidadVendida,
        BigDecimal montoTotal) {
}
