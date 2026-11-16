package pe.edu.pe.PharmaBackend.reportes.dto;

import java.math.BigDecimal;

public record ProductoMasVendidoDTO(
        Long productoId,
        String productoNombre,
        Long cantidadVendida,
        BigDecimal montoTotal) {
}
