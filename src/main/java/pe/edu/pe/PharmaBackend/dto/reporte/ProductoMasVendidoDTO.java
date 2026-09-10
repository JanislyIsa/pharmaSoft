package pe.edu.pe.PharmaBackend.dto.reporte;

import java.math.BigDecimal;

public record ProductoMasVendidoDTO(
        Long productoId,
        String productoNombre,
        String categoriaNombre,
        Long cantidadVendida,
        BigDecimal montoTotal
) {
}