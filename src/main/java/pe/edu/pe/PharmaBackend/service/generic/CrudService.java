package pe.edu.pe.PharmaBackend.service.generic;

import pe.edu.pe.PharmaBackend.dto.ClienteResponseDTO;

public interface CrudService<REQ, RES, ID> {
    RES create(REQ t);
    RES update(ID id, REQ t);
    ClienteResponseDTO read(ID id);
    void delete(ID id);
    Iterable<RES> readAll();
}