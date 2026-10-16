package pe.edu.pe.PharmaBackend.service.service;

import pe.edu.pe.PharmaBackend.dto.VentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.VentaResponseDTO;
import pe.edu.pe.PharmaBackend.enums.EstadoVenta;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.time.LocalDate;
import java.util.List;

public interface VentaService {
    VentaResponseDTO registrar(VentaRequestDTO request);
    VentaResponseDTO buscar(Long id);
    Page<VentaResponseDTO> buscar(Long clienteId, EstadoVenta estado, LocalDate desde, LocalDate hasta, Pageable pageable);
    List<VentaResponseDTO> listar();
    VentaResponseDTO anular(Long id);   // <-- agregar esta línea
}
