package pe.edu.pe.PharmaBackend.service.service;

import pe.edu.pe.PharmaBackend.dto.VentaRequestDTO;
import pe.edu.pe.PharmaBackend.dto.VentaResponseDTO;

import java.util.List;

public interface VentaService {
    VentaResponseDTO registrar(VentaRequestDTO request);
    VentaResponseDTO buscar(Long id);
    List<VentaResponseDTO> listar();
    VentaResponseDTO anular(Long id);   // <-- agregar esta línea
}