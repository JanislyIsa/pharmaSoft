package pe.edu.pe.PharmaBackend.service.service;

import pe.edu.pe.PharmaBackend.dto.VentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.VentaResponseDTO;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;

import java.time.LocalDateTime;
import java.util.List;

public interface VentaService {
    VentaResponseDTO registrar(VentaRequestDTO request);
    VentaResponseDTO buscar(Long id);
    List<VentaResponseDTO> listar();
    VentaResponseDTO anular(Long id);
    List<VentaResponseDTO> buscar(
            Long ClienteId,
            EstadoVenta Estado,
            LocalDateTime desde,
            LocalDateTime hasta
    );
}