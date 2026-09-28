package pe.edu.pe.PharmaBackend.service.service;

import pe.edu.pe.PharmaBackend.dto.ClienteRequestDTO;
import pe.edu.pe.PharmaBackend.dto.ClienteResponseDTO;
import pe.edu.pe.PharmaBackend.dto.PaginaResponseDTO;
import pe.edu.pe.PharmaBackend.service.generic.CrudService;
import org.springframework.data.domain.Pageable;

public interface ClienteService extends CrudService<ClienteRequestDTO, ClienteResponseDTO, Long> {
    PaginaResponseDTO<ClienteResponseDTO> listar(Pageable pageable);
}
